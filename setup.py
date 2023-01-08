import setuptools

with open("README.md", "r",encoding='utf-8') as f:
  long_description = f.read()

setuptools.setup(
    name='nonebot_plugin_cave',
    version='1.0.3',
    description='cave plugin in Nonebot2',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='hmzz804',
    author_email='2166908863@qq.com',
    url='https://github.com/hmzz804/nonebot_plugin_cave',
    install_requires=[
        'nonebot2>=2.0.0-beta.2',
        'nonebot-adapter-onebot>=2.0.0b1',
        'nonebot-adapter-onebot',
        'requests',
	],
    license='MIT License',
    packages=setuptools.find_packages(),
	entry_points={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

