#!/bin/bash
cd /home/kavia/workspace/code-generation/medical-decision-support-chatbot-2953-2962/fastapi_backend
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

