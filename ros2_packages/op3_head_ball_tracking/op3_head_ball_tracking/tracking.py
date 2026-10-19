"""Track the ball with OP3 head IDs 19/20, or compute commands in dry-run mode."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import psutil
import threading
import time
import uuid
from collections import deque
from contextlib import ExitStack, nullcontext
from datetime import datetime, timezone
from pathlib import Path

import cv2
import rclpy
from ultralytics import YOLO

from op3_live_monitor.monitor import CameraNode, COLORS, NAMES, REPO_ROOT, SharedState, render, validate_model
from .bus import HARD_LIMITS, HeadActuator, HeadBus, raw_to_rad

COLUMNS = (
    'frame_index', 'capture_stamp_ns', 'processed_at_utc', 'ball_confidence',
    'ball_track_id', 'ball_center_x', 'ball_center_y', 'error_x_norm', 'error_y_norm',
    'lock_frames', 'camera_age_ms', 'inference_ms', 'processing_ms',
    'target_pan_deg', 'target_tilt_deg', 'present_pan_deg', 'present_tilt_deg',
    'process_cpu_percent', 'system_cpu_percent', 'process_ram_mib',
    'system_ram_percent', 'fps', 'command_computed', 'hardware_write', 'reason',
)
WINDOW = 'OP3 HEAD 19/20 - BALL TRACKING - q/Esc keluar'


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manager_active() -> bool:
    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            name = process.info['name'] or ''
            command = process.info['cmdline'] or []
            if name == 'op3_manager' or any(part.endswith('/op3_manager') for part in command):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def bounded_goal(current: float, initial: float, error: float, joint_id: int,
                 excursion: float) -> float:
    if abs(error) < 0.08:
        return current
    step = max(-0.025, min(0.025, -0.045 * error))
    lower, upper = HARD_LIMITS[joint_id]
    return max(lower, initial - excursion,
               min(upper, initial + excursion, current + step))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topic', default='/thesis/image_raw')
    parser.add_argument('--duration', type=float, default=30)
    parser.add_argument('--enable-motion', action='store_true',
                        help='Actually control only IDs 19/20 after hardware preflight')
    parser.add_argument('--no-preview', action='store_true')
    parser.add_argument('--run-root', type=Path, default=REPO_ROOT / 'runs/op3_head_ball_tracking')
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--conf', type=float, default=0.25)
    parser.add_argument('--iou', type=float, default=0.45)
    parser.add_argument('--ball-control-conf', type=float, default=0.5)
    parser.add_argument('--max-excursion-deg', type=float, default=12)
    args = parser.parse_args()
    if args.duration <= 0 or args.imgsz <= 0 or not 0 <= args.conf <= 1 or not 0 <= args.iou <= 1:
        parser.error('Invalid duration/imgsz/conf/iou')
    if not 0 <= args.ball_control_conf <= 1 or not 0 < args.max_excursion_deg <= 20:
        parser.error('Invalid ball-control-conf/max-excursion-deg')
    if not args.no_preview and not os.environ.get('DISPLAY'):
        parser.error('DISPLAY empty; use SSH -X or --no-preview')
    if args.enable_motion and manager_active():
        parser.error('op3_manager is active; direct U2D2 access would conflict')

    checkpoint, digest, offline = validate_model(REPO_ROOT)
    model = YOLO(str(checkpoint), task='detect')
    if {int(k): str(v) for k, v in model.names.items()} != NAMES:
        raise ValueError('Checkpoint class mapping mismatch')
    model.to('cpu')
    model.model.float()
    model.model.eval()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:6]
    run_dir = args.run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    meta_path = run_dir / 'summary.json'
    meta = {
        'status': 'starting', 'run_id': run_id, 'started_at_utc': utc_now(),
        'mode': 'hardware_head_only' if args.enable_motion else 'dry_run_no_motion',
        'topic': args.topic, 'checkpoint_sha256': digest,
        'head_ids': {'head_pan': 19, 'head_tilt': 20},
        'duration_requested_s': args.duration, 'imgsz': args.imgsz,
        'conf': args.conf, 'iou': args.iou,
        'ball_control_conf': args.ball_control_conf,
        'max_excursion_deg': args.max_excursion_deg,
        'no_image_video_saved': True,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + '\n')
    state = SharedState()
    node = None
    spin_thread = None
    window_open = False
    started = None
    frames = ball_frames = computed = hardware_writes = 0
    process = psutil.Process()
    process.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None)
    last_resource = 0.0
    resources = {}
    initial = {19: 0.0, 20: math.radians(-10)}
    target = dict(initial)
    lock_id = None
    lock_frames = 0
    last_command = 0.0
    history: deque[dict] = deque(maxlen=60)
    last_history = 0.0
    actuator = None
    exit_reason = 'duration_elapsed'
    fatal = None
    bus_context = HeadBus() if args.enable_motion else nullcontext()
    bus = bus_context if args.enable_motion else None
    try:
        with ExitStack() as stack:
            bus = stack.enter_context(bus_context)
            stream = stack.enter_context((run_dir / 'tracking.csv').open('x', newline=''))
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            if args.enable_motion:
                actuator = HeadActuator(bus, math.radians(args.max_excursion_deg))
                stack.callback(actuator.restore)
                servo_info = actuator.prepare()
                meta['servo_preflight'] = servo_info
                initial = {19: raw_to_rad(actuator.initial_raw[19]),
                           20: raw_to_rad(actuator.initial_raw[20])}
                target = dict(initial)
            rclpy.init()
            node = CameraNode(state, args.topic)
            spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
            if not args.no_preview:
                cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(WINDOW, 1100, 720)
                window_open = True
            spin_thread.start()
            started = time.monotonic()
            meta['status'] = 'running'
            meta_path.write_text(json.dumps(meta, indent=2) + '\n')
            print(f'Tracking: {run_dir}; mode={meta["mode"]}; duration={args.duration}s', flush=True)
            while time.monotonic() - started < args.duration:
                item = state.take_latest() if state.new_frame.is_set() else None
                if item is not None:
                    frame, stamp_ns = item
                    tick = time.perf_counter()
                    result = model.track(source=frame, imgsz=args.imgsz, batch=1,
                                         device='cpu', conf=args.conf, iou=args.iou,
                                         tracker='botsort.yaml', persist=True,
                                         verbose=False, save=False, plots=False,
                                         stream=False, max_det=300)[0]
                    annotated = frame.copy()
                    counts = {name: 0 for name in NAMES.values()}
                    detections = []
                    ball = None
                    for box in result.boxes if result.boxes is not None else []:
                        class_id = int(box.cls.item())
                        name = NAMES[class_id]
                        score = float(box.conf.item())
                        track_id = int(box.id.item()) if box.id is not None else None
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        counts[name] += 1
                        detections.append({'class': name, 'confidence': round(score, 4),
                                           'track_id': track_id})
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), COLORS[name], 2)
                        text = f'{name} #{track_id} {score:.2f}'
                        cv2.putText(annotated, text, (x1, max(y1 - 7, 16)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[name], 2, cv2.LINE_AA)
                        if class_id == 0 and (ball is None or score > ball[0]):
                            ball = (score, track_id, (x1 + x2) / 2, (y1 + y2) / 2)
                    now = time.monotonic()
                    age = (time.time_ns() - stamp_ns) / 1e6 if stamp_ns > 0 else None
                    if age is not None and not 0 <= age <= 1000:
                        age = None
                    ex = ey = None
                    issued = False
                    written = False
                    readback = {}
                    reason = 'no_ball'
                    if ball is not None:
                        ball_frames += 1
                        score, track_id, cx, cy = ball
                        ex = 2 * cx / frame.shape[1] - 1
                        ey = 2 * cy / frame.shape[0] - 1
                        if track_id is not None and track_id == lock_id:
                            lock_frames += 1
                        else:
                            lock_id = track_id
                            lock_frames = 1 if track_id is not None else 0
                        if score < args.ball_control_conf:
                            reason = 'low_confidence'
                        elif lock_frames < 3:
                            reason = 'await_track_lock'
                        elif age is None or age > 300:
                            reason = 'stale_frame'
                        elif now - last_command < 0.2:
                            reason = 'rate_limit'
                        else:
                            new_pan = bounded_goal(target[19], initial[19], ex, 19,
                                                   math.radians(args.max_excursion_deg))
                            new_tilt = bounded_goal(target[20], initial[20], ey, 20,
                                                    math.radians(args.max_excursion_deg))
                            if abs(new_pan - target[19]) > 1e-6 or abs(new_tilt - target[20]) > 1e-6:
                                target = {19: new_pan, 20: new_tilt}
                                issued = True
                                computed += 1
                                if actuator is not None:
                                    writes_before = bus.write_count
                                    actual = actuator.command(new_pan, new_tilt)
                                    target = {19: actual['head_pan'], 20: actual['head_tilt']}
                                    hardware_writes = bus.write_count
                                    written = bus.write_count > writes_before
                                    readback = {19: raw_to_rad(bus.read(19, 132, 4)),
                                                20: raw_to_rad(bus.read(20, 132, 4))}
                                    if any(abs(readback[i] - target[i]) > 0.25 for i in (19, 20)):
                                        raise RuntimeError('Head readback too far from bounded goal')
                                reason = 'commanded' if written else 'dry_run_command'
                            else:
                                reason = 'deadband_or_limit'
                            last_command = now
                    else:
                        lock_id = None
                        lock_frames = 0
                    if now - last_resource >= 1:
                        resources = {
                            'process_cpu_percent': round(process.cpu_percent(interval=None), 1),
                            'system_cpu_percent': round(psutil.cpu_percent(interval=None), 1),
                            'process_ram_mib': round(process.memory_info().rss / (1024 * 1024), 1),
                            'system_ram_percent': round(psutil.virtual_memory().percent, 1),
                        }
                        last_resource = now
                    processing_ms = (time.perf_counter() - tick) * 1000
                    cv2.putText(annotated,
                                f'HEAD pan {math.degrees(target[19]):+.1f} tilt {math.degrees(target[20]):+.1f} deg',
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
                    state.record(annotated, {
                        'counts': counts, 'detections': detections,
                        'inference_ms': round(float(result.speed.get('inference', 0)), 2),
                        'preprocess_ms': round(float(result.speed.get('preprocess', 0)), 2),
                        'postprocess_ms': round(float(result.speed.get('postprocess', 0)), 2),
                        'end_to_end_ms': round(processing_ms, 2),
                        'camera_age_ms': round(age, 1) if age is not None else None,
                        **resources,
                    })
                    _, current_metrics = state.snapshot()
                    frames += 1
                    writer.writerow({
                        'frame_index': frames, 'capture_stamp_ns': stamp_ns,
                        'processed_at_utc': utc_now(),
                        'ball_confidence': round(ball[0], 4) if ball else '',
                        'ball_track_id': ball[1] if ball and ball[1] is not None else '',
                        'ball_center_x': round(ball[2], 1) if ball else '',
                        'ball_center_y': round(ball[3], 1) if ball else '',
                        'error_x_norm': round(ex, 4) if ex is not None else '',
                        'error_y_norm': round(ey, 4) if ey is not None else '',
                        'lock_frames': lock_frames,
                        'camera_age_ms': round(age, 1) if age is not None else '',
                        'inference_ms': round(float(result.speed.get('inference', 0)), 2),
                        'processing_ms': round(processing_ms, 2),
                        'target_pan_deg': round(math.degrees(target[19]), 2),
                        'target_tilt_deg': round(math.degrees(target[20]), 2),
                        'present_pan_deg': round(math.degrees(readback[19]), 2) if readback else '',
                        'present_tilt_deg': round(math.degrees(readback[20]), 2) if readback else '',
                        'process_cpu_percent': resources.get('process_cpu_percent', ''),
                        'system_cpu_percent': resources.get('system_cpu_percent', ''),
                        'process_ram_mib': resources.get('process_ram_mib', ''),
                        'system_ram_percent': resources.get('system_ram_percent', ''),
                        'fps': round(current_metrics['fps'], 2),
                        'command_computed': int(issued), 'hardware_write': int(written),
                        'reason': reason,
                    })
                    stream.flush()
                frame_out, metrics = state.snapshot()
                now = time.monotonic()
                if now - last_history >= 1:
                    history.append(metrics)
                    last_history = now
                if window_open:
                    cv2.imshow(WINDOW, render(frame_out, metrics, history, offline, args.topic))
                    if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                        exit_reason = 'operator_stopped'
                        break
                    if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                        exit_reason = 'window_closed'
                        break
                elif item is None:
                    time.sleep(0.01)
    except KeyboardInterrupt:
        exit_reason = 'keyboard_interrupt'
    except Exception as error:
        fatal = repr(error)
        exit_reason = 'error'
        print(f'Tracking error: {fatal}', flush=True)
    finally:
        if bus is not None:
            hardware_writes = bus.write_count
        if actuator is not None and actuator.restore_report:
            meta['servo_restore'] = actuator.restore_report
        state.running.clear()
        if rclpy.ok():
            rclpy.shutdown()
        if spin_thread and spin_thread.is_alive():
            spin_thread.join(timeout=3)
        if node is not None:
            node.destroy_node()
        if window_open:
            cv2.destroyAllWindows()
        # ExitStack restores head joints before closing the serial port.
        meta.update({
            'status': 'completed' if fatal is None and frames > 0 and exit_reason == 'duration_elapsed'
                      else 'stopped_early' if fatal is None else 'incomplete',
            'stop_reason': exit_reason, 'fatal_error': fatal,
            'stopped_at_utc': utc_now(), 'processed_frames': frames,
            'ball_frames': ball_frames, 'computed_commands': computed,
            'hardware_writes': hardware_writes,
            'actual_loop_duration_s': round(time.monotonic() - started, 2) if started else None,
        })
        meta_path.write_text(json.dumps(meta, indent=2) + '\n')
        print(f'Tracking selesai: {run_dir}; frames={frames}; ball={ball_frames}; '
              f'computed={computed}; hardware_writes={hardware_writes}', flush=True)
    return 0 if meta['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
