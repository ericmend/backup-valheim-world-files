export OLD_PWD=$(pwd)
cd $(dirname $0)
export VENV=.venv
if ! [ -d $VENV ]; then
    make init
fi
source $VENV/bin/activate
$VENV/bin/python3 -B app/main.py --world 'flere' --path '/home/ubuntu/.config/unity3d/IronGate/Valheim/worlds' \
    --drive_folder '1LPcMMx6r-8IKx4quBj5UKipC2c4pkFAV' --service_account_file 'credentials.json'
unset VENV
cd $OLD_PWD