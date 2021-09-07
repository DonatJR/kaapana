echo '==============================='
echo 'Run an awesome M2aia Application'
echo '==============================='
env QTWEBENGINE_DISABLE_SANDBOX=1 /m2aia/M2aia.sh &
PID=$!
# wait until Workbench is ready
tail -f  /root/Desktop/logfile | while read LOGLINE
do
	[[ "${LOGLINE}" == *"BlueBerry Workbench ready"* ]] && pkill -P $$ tail
done
echo 'Setting fullscreen mode'
wmctrl -r 'Research' -b toggle,fullscreen
# wait for process to end, before starting new process
wait $PID
#clear logfile
> /root/Desktop/logfile



