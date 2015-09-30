#!/bin/sh

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ -n "`$SHELL -c 'echo $ZSH_VERSION'`" ]; then
  echo "export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY:'$DIR/modules/'" >> ~/.zshrc
  echo "export GDEPLOY_TEMPLATES='$DIR'" >> ~/.zshrc
elif [ -n "`$SHELL -c 'echo $BASH_VERSION'`" ]; then
  echo "export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY:'$DIR/modules/'" >> ~/.bashrc
  echo "export GDEPLOY_TEMPLATES='$DIR'" >> ~/.bashrc
fi

python $DIR/setup.py install
