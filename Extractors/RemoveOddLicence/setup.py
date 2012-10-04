#!/usr/bin/python

from distutils.core import setup
import py2exe

#sys.path.append("C:\Windows\winsxs\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.4926_none_508ed732bcbc0e5a")

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
    version="0.64.1.0"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>Grid 2 Licence Checker</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.30729.4926"
            processorArchitecture="X86"
            publicKeyToken="1fc8b3b9a1e18e3b"
            language="*"
        />
    </dependentAssembly>
</dependency>   
</assembly>
"""

"""
installs manifest and icon into the .exe
but icon is still needed as we open it
for the window icon (not just the .exe)
changelog and logo are included in dist
"""



setup(
    data_files=data_files,
    windows = [
        {
            "script": "RemoveOddLicenceWx.py",
            "icon_resources": [(1, "icon.ico")],
            "other_resources": [(24,1,manifest)]
        }
    ],
      data_files=["icon.ico"]
)
  