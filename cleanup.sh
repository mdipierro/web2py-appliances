
rm */sessions/*
rm */errors/*
rm */databases/*
rm */cache/*
rm -r models views controllers cache errors sessions uploads static ABOUT LICENSE tests cron modules languages databases private

find ./ -name '*~' -exec rm -f {} \; 
find ./ -name '*.orig' -exec rm -f {} \; 
find ./ -name '*.rej' -exec rm -f {} \; 
find ./ -name '*.bak' -exec rm -f {} \; 
find ./ -name '*.bak2' -exec rm -f {} \; 
find ./ -name '#*' -exec rm -f {} \;
