# Senior-project-tacobell

create python venv to keep local env clean
python3 -m venv myenv

on mac
source myenv/bin/activate

on windows
myenv\Scripts\activate

pip3 install -r "requirements.txt"

streamlit run taco_bell_streamlit.py

to check if db is running and which port
ps aux | grep mongod


for mongo

step 1
mongod --config /opt/homebrew/etc/mongod.conf

step 2
use tacobell

step 3
show collections

step 4
db.menu.find().pretty()


to download
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew tap mongodb/brew
brew install mongodb-community@6.0


brew services start mongodb/brew/mongodb-community
(if you get error) --> mongod --config /opt/homebrew/etc/mongod.conf
