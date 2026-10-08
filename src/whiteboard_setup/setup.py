from setuptools import setup

package_name = "whiteboard_setup"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/spawn_whiteboard.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Evan Kusa",
    maintainer_email="evankusa@gmail.com",
    description="The midterm whiteboard station for Gazebo and MoveIt, and the marker adapter.",
    license="BSD-3-Clause",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "whiteboard_scene = whiteboard_setup.scene_whiteboard:main",
            "attach_pen = whiteboard_setup.attach_pen:main",
        ],
    },
)
