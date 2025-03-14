# Synology API Integration

I created this to privatize and archive my photos from Google. I will try to make scripts modular so that they may be
reused for other purposes. The synology API has been rather difficult to integrate with as there are not very many
examples and barely any documentation. 

# Troubleshooting Help

- If creating a tag based album fails, ensure that there are photos with the tag first. It is not possible to create an
  empty tag based album

## SSH To Diskstation Server

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

