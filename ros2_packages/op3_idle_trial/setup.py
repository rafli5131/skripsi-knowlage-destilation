from setuptools import find_packages, setup

package_name = "op3_idle_trial"
setup(name=package_name, version="0.1.0", packages=find_packages(),
      data_files=[("share/ament_index/resource_index/packages", ["resource/" + package_name]),
                  ("share/" + package_name, ["package.xml"])],
      install_requires=["setuptools"], zip_safe=True,
      maintainer="BhreW", maintainer_email="BhreW@users.noreply.github.com",
      description="Metadata-only OP3 live tracking trial", license="MIT",
      entry_points={"console_scripts": ["op3-idle-trial = op3_idle_trial.trial:main"]})
