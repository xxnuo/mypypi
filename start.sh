#!/bin/sh

cd /app

echo "======================================================"
if [ "${PYPI_BROWSER_OFF}" != "true" ]; then
echo "Serving pypi webui on http://${PYPI_BROWSER_HOST}:${PYPI_BROWSER_PORT}"
fi
echo "Serving pypi server on http://${PYPI_HOST}:${PYPI_PORT}/simple"
echo "======================================================"

if [ "${PYPI_BROWSER_OFF}" != "true" ]; then
uvicorn pypi_browser.app:app --host ${PYPI_BROWSER_HOST} --port ${PYPI_BROWSER_PORT} --log-level warning &
fi

pypi-server run -i ${PYPI_HOST} -p ${PYPI_PORT} --fallback-url ${PYPI_UPSTREAM} -- ${PYPI_LOCAL_PACKAGES_DIR}
