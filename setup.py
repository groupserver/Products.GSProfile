# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='Products.GSProfile',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='Michael JasonSmith',
      author_email='mpj17@onlinegroups.net',
      url='http://groupserver.org',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'AccessControl',
          'five.formlib',
          'gs.content.form',
          'gs.database',
          'gs.profile.base',
          'gs.profile.email.base',
          'gs.profile.notify',
          'Zope2',
          'Products.CustomUserFolder',
          'Products.GSAuditTrail',
          'Products.XWFCore',
          'pytz',
          'zope.app.apidoc',
          'zope.app.form',
          'zope.app.publisher',
          'zope.cachedescriptors',
          'zope.component',
          'zope.contentprovider',
          'zope.formlib',
          'zope.interface',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.viewlet',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
