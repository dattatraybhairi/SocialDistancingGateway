#! /bin/bash/


sudo systemctl daemon-reload

sudo systemctl enable broker.service
sudo systemctl enable counter.service
sudo systemctl enable gateway.service

sudo systemctl start broker.service
sudo systemctl start counter.service
sudo systemctl start gateway.service