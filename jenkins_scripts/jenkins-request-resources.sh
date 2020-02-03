#!/usr/bin/env bash

#-----------------------------------------------------------------------------

if [ ! "$1" ];then
    echo "ERROR: Usage $0 con|vm|all [5m|10h|7d]"
    exit 1
fi

if [ ! "$UUID" ];then
    echo "ERROR: UUID is not set!"
    exit 1
fi

WAIT="${WAIT:-259200}"      # 3 days in seconds

if [ "$WAIT" != "259200" ];then
    WAIT_DIGIT=`echo $WAIT | grep -E -o "[0-9]+"`
    WAIT_PREFIX=`echo $WAIT | grep -E -o "[mhd]"`

    if [ ! "$WAIT_DIGIT" ] || [ ! "$WAIT_PREFIX" ];then
        exit 1
    fi

    if [ "$WAIT_PREFIX" = "m" ];then
        WAIT=$((WAIT_DIGIT*60))
    elif [ "$WAIT_PREFIX" = "h" ];then
        WAIT=$((WAIT_DIGIT*60*60))
    elif [ "$WAIT_PREFIX" = "d" ];then
        WAIT=$((WAIT_DIGIT*24*60*60))
    fi

    if [ "$WAIT" -gt "259200" ];then
        echo "ERROR: Waiting threshold reached!"
        exit 1
    fi
fi

#-----------------------------------------------------------------------------

QUEUE_DIR="/status/queue"

BUILD_EMAIL="${BUILD_USER_EMAIL:-none}"
BUILD_NAME="${JOB_NAME:-none}"
BUILD_NUMBER="${BUILD_NUMBER:-none}"
BUILD_URL="${BUILD_URL:-none}"
PRIORITY="${PRIORITY:-low}"
RESOURCE="$1"
TIMESTAMP=`date +%s`

#-----------------------------------------------------------------------------

echo "INFO: TASK UUID: ${UUID}"
echo "${PRIORITY};${RESOURCE};${BUILD_NAME};${BUILD_NUMBER};${BUILD_EMAIL};${BUILD_URL};${TIMESTAMP}" > "${QUEUE_DIR}/waiting/${UUID}"

#-----------------------------------------------------------------------------

COUNT=0

while [ "True" ];do
    if [ -f "${QUEUE_DIR}/waiting/${UUID}" ];then
        COUNT=$((COUNT+1))
        sleep 1
    else
        break
    fi

    if [ "$COUNT" -gt "$WAIT" ];then
        echo "ERROR: Timeout occured"
        exit 1
    fi
done