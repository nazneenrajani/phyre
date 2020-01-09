## Useful Links
[Collision detection](https://www.iforce2d.net/b2dtut/collision-callbacks)
[Box2D Classes](https://documentation.help/Box2D/annotated.htm)

## Installation

Based on [Phyre INSTALLATION.md](https://github.com/facebookresearch/phyre/blob/master/INSTALLATION.md).
Make sure you have Anaconda or Miniconda installed.


```bash
git clone https://github.com/facebookresearch/phyre.git
cd phyre
```
Replace env.yml with this one, then run. This step might not be necessary, but when I tried it with their's, I was missing a lot of dependencies.
```bash
conda env create -f env.yml
conda activate phyre
```

Copy the src files into their phyre directories (replacing when prompted).

You don't need to wait for the entire make process to finish, since it deletes the large data sets and recompiles it every time. I typically just abort (^C) at "[100%]" when the next line is "rm -rf ..."

```bash
make
```

## Usage

I choose not to install phyre as a library to make testing and compiling easier, so any python files like 'run_sim.py' need to be run within src/python.

There are alternatives to some blocks of code, so make sure you read the comments in the file before you run it.

```bash
cd src/python
python run_sim.py
```
