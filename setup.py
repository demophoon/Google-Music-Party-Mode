import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'pyramid_beaker',
    'gmusicapi',
    'gevent==1.0',
    'gevent-websocket==0.3.6',
    'pyramid-sockjs',
]

setup(name='gmusic',
      version='0.0',
      description='gmusic',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='gmusic',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = gmusic:main
      [console_scripts]
      initialize_gmusic_db = gmusic.scripts.initializedb:main
      load_songs_gmusic_db = gmusic.scripts.load_songs:main
      """,
      )
