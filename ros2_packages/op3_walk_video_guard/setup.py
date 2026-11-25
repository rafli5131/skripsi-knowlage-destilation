from setuptools import find_packages, setup

name = "op3_walk_video_guard"
setup(name=name, version="0.1.0", packages=find_packages(),
      data_files=[("share/ament_index/resource_index/packages", ["resource/" + name]),
                  ("share/" + name, ["package.xml"])],
      install_requires=["setuptools"], zip_safe=True,
      maintainer="BhreW", maintainer_email="BhreW@users.noreply.github.com",
      description="Guard video berjalan OP3 dengan batas encoder kepala", license="MIT")
