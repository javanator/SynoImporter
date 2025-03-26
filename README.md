# What this is

I created this to privatize and archive my photos from Google. I will try to make scripts modular so that they may be
reused for other purposes. The synology API has been rather difficult to integrate with as there are not very many
examples and barely any documentation.

Currently, API integration is functional, but overall script to import a Google takeout file contents is a work in
progress

# Errata
```
sudo apt install libexiv2-dev libboost-python-dev
```


Synology photos stores tags as IPTC data in a field called "keywords". If scripting tag based albums, an optimization
may be to write the keywords to the jpeg files prior to upload. This would save on network round-trips.

# Troubleshooting Help

- If creating a tag based album fails, ensure that there are photos with the tag first. It is not possible to create an
  empty tag based album

## SSH To Diskstation Server

This log file will show API activity and will sometimes provide more error details than what is returned in the HTTP
response

```
sudo vi /var/log/synoscgi.log
```

# References

[Synology DSM API Reference]( https://global.download.synology.com/download/Document/Software/DeveloperGuide/Os/DSM/All/enu/DSM_Login_Web_API_Guide_enu.pdf )

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

