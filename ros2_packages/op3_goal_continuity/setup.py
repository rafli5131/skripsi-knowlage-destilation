from setuptools import find_packages, setup

name = 'op3_goal_continuity'
setup(name=name, version='0.1.0', packages=find_packages(),
      data_files=[('share/ament_index/resource_index/packages', ['resource/'+name]),
                  ('share/'+name, ['package.xml'])], install_requires=['setuptools'],
      zip_safe=True, maintainer='BhreW', maintainer_email='BhreW@users.noreply.github.com',
      description='Estimasi gawang sementara untuk preview OP3', license='MIT')
