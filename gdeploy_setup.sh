#!/bin/sh

test `id -u` -ne 0  && echo "Only root can run setup." && exit 1
PLUGIN_DIR=/usr/lib/python2.7/site-packages/ansible/plugins/callback/

PLUGIN_DIR=/usr/lib/python2.7/site-packages/ansible/plugins/callback/

update_init_file ()
{
    INIT_FILE="$1"

    # Clean up the stale environment variables
    sed -i '/^export ANSIBLE_LIBRARY=/'d $INIT_FILE
    sed -i '/^export GDEPLOY_TEMPLATES=/'d $INIT_FILE

    echo "export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY:'$DIR/modules/'" >>$INIT_FILE
    echo "export GDEPLOY_TEMPLATES='$DIR'" >> $INIT_FILE
}

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ -n "`$SHELL -c 'echo $ZSH_VERSION'`" ]; then
    update_init_file "$HOME/.zshrc"
elif [ -n "`$SHELL -c 'echo $BASH_VERSION'`" ]; then
    update_init_file "$HOME/.bashrc"
fi

# Copy the plugins to ansible plugin directory
cp -f $DIR/plugins/callback/gdeploy.py $PLUGIN_DIR

python $DIR/setup.py install
echo; echo
echo -n "Please run the command 'source $INIT_FILE'  to "
echo "update the environment variables."
