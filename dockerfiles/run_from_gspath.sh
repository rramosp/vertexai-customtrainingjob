#!/bin/bash

if [[ -v ZIP_WITH_RUNSCRIPT_GSPATH ]]; then
  export gspath=$ZIP_WITH_RUNSCRIPT_GSPATH
  echo "--- copying zip from $ZIP_WITH_RUNSCRIPT_GSPATH"
  gsutil cp $ZIP_WITH_RUNSCRIPT_GSPATH zip_with_runscript.zip
  echo "--- unzipping"
  unzip -o zip_with_runscript.zip

  if [ -f run.sh ]; then

    echo "--- running run.sh"
    chmod 755 run.sh
    ./run.sh
  else
    echo "no run.sh found in zip file"
    exit 1
  fi

else
  echo "must define ZIP_WITH_RUNSCRIPT_GSPATH with a gsuri to a zip file containing a run.sh file"
  exit 1
fi
