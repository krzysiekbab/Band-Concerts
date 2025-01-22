## Deployment instructions with Nginx and Gunicorn.
### Set up project directory
**Install dependencies on the server:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx -y
```

**Set up the Python environment:**
```bash
cd /var/www/Concert-App
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


### Test the application locally
```bash
gunicorn --bind 0.0.0.0:8000 run:app
```

### Configure Gunicorn as a Systemd Service
```bash
sudo vim /etc/systemd/system/concert_app.service
```

**Add the following configuration:**

```ini
[Unit]
Description=Gunicorn instance to serve Concert-App
After=network.target

[Service]
User=<your_user>>
Group=<your_group>
WorkingDirectory=/var/www/Concert-App
Environment="PATH=/var/www/Concert-App/venv/bin"
ExecStart=/var/www/Concert-App/venv/bin/gunicorn --workers 3 --bind unix:/var/www/Concert-App/concert_app.sock run:app

[Install]
WantedBy=multi-user.target
```

**Reload systemd to recognize the new service:**
```bash
sudo systemctl daemon-reload
```
**Start and enable the Gunicorn service:**
```bash
sudo systemctl start concert_app
sudo systemctl enable concert_app
```

### Configure Nginx
```bash
sudo vim /etc/nginx/sites-available/concert_app
```

**Add the following configuration:**

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://unix:/var/www/Concert-App/concert_app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/Concert-App/app/static/;
    }

    error_page 404 /404.html;
    error_page 500 /500.html;
}
```

**Test Nginx configuration:**

```bash
sudo nginx -t
```

**Restart Nginx:**

```bash
sudo systemctl restart nginx
```

### Summary of Key Paths for Concert-App

- **Project Directory**: `/var/www/Concert-App`
- **Gunicorn Socket**: `/var/www/Concert-App/concert_app.sock`
- **Gunicorn Service**: `/etc/systemd/system/concert_app.service`
- **Nginx Config**: `/etc/nginx/sites-available/concert_app`

This adjusted setup will host your Concert-App on Ubuntu with Nginx and Gunicorn.

### Helpful Commands
**Check the status of the Gunicorn service:**

```bash
sudo systemctl status concert_app
```

**Check the logs of the service to see any errors:**

```bash
sudo journalctl -u concert_app
```