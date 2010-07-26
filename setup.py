try:
    from setuptools import Command, find_packages, setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import Command, find_packages, setup

class data(Command):

    description = "Process databases into the structures used by xpaxs"

    user_options = []

    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        for db, fname in {
            'elamdb': 'ElamDB12.zip',
            'henkedb': 'HenkeDB.tar.gz',
            'waasmaierdb': 'WaasmaierDB.tar.gz',
            }.iteritems():
            subprocess.call(
                [
                    'python',
                    'data/process_%s.py' % db,
                    'data/%s' % fname,
                    'xpaxs/phys_ref_data/phys_ref_data'
                    ]
                )
        

setup(
    author = 'Darren Dale',
    author_email = 'darren.dale@cornell.edu',
    cmdclass = {'data': data},
    description = 'Extensible packages for x-ray science',
    install_requires = (
        'numpy >= 1.4.0',
        'quantities >= 0.9.0',
        'scipy >= 0.7.0',
        'h5py >= 1.3.0',
        ),
    license = 'BSD',
    name = 'xpaxs',
    package_data = {
        '': ['*.h5'],
        },
    packages = find_packages(),
    requires = (
        'python (>=2.6, <3.0)',
        'hdf5 (>=1.8.5)',
        'PyQt (>= 4.7.4)',
        'dip (> 0.1.0)',
        ),
    test_suite = 'nose.collector',
    version = '0.11.0',
)
