if [ ! -f prev_head ]; # initialize if this is the 1st poll
then
  git rev-parse master > prev_head
fi
# fetch & merge, then inspect head
git fetch  > build_log.txt 2>&1
if [ $? -eq 0 ]
then
  echo "Fetch from git done";
  git merge FETCH_HEAD >> build_log.txt 2>&1 ;
  git rev-parse master > latest_head
  if ! diff latest_head prev_head > /dev/null ;
  then
    echo "Merge via git done"; ...
    cat latest_head > prev_head # update stored HEAD
    # there has been a change, build
  fi
fi
