# Compare to see whether the US_EPA data files are the same

START_YEAR=2005
END_YEAR=2020

DIR_ONE="/data/high_res/US_EPA/NO2"
DIR_TWO="/data/high_res/emacdonald/unet/datafiles/US_EPA/"

# Loop through the years and compare the files
for YEAR in $(seq $START_YEAR $END_YEAR); do
    FILE_ONE="$DIR_ONE/daily_42602_$YEAR.csv"
    FILE_TWO="$DIR_TWO/daily_42602_$YEAR.csv"
    
    if [ -f "$FILE_ONE" ] && [ -f "$FILE_TWO" ]; then
        if cmp -s "$FILE_ONE" "$FILE_TWO"; then
            echo "Files for year $YEAR are the same."
        else
            echo "Files for year $YEAR differ!"
        fi
    else
        echo "One of the files for year $YEAR does not exist."
    fi
done