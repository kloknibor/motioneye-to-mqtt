docker run --rm \
    -v "${PWD}:/src" \
    six8/pyinstaller-alpine \
    --noconfirm \
    --onefile \
    --log-level DEBUG \
    --clean \
    motioneye-to-mqtt.py