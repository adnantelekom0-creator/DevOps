#!/usr/bin/env groovy

/**
 * Standardize logging format across all enterprise pipelines
 * Usage: logInfo("Message to log")
 */
def call(String message) {
    def timestamp = new Date().format('yyyy-MM-dd HH:mm:ss', TimeZone.getTimeZone('UTC'))
    echo "[DEVOPS-AUDIT] [${timestamp} UTC] => ${message}"
}
