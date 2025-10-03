from setuptools import setup

package_name = "whiteboard_setup"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/urdf", ["urdf/whiteboard_setup.urdf.xacro"]),
        ("share/" + package_name + "/meshes", ["meshes/whiteboard.stl"]),
        ("share/" + package_name + "/launch", ["launch/spawn_whiteboard.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="YOUR NAME",
    maintainer_email="YOUR EMAIL",
    description="Description package for whiteboard object (URDF, mesh, launch).",
    license="BSD-3-Clause",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "whiteboard_scene = whiteboard_setup.scene_whiteboard:main",
            "attach_pen = whiteboard_setup.attach_pen:main"
        ],
    },
)

