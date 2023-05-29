for year in 10 11 12 13 14 15 16 17 18 19 20 21 22 23
do
    echo "Querying 20$year field reports"
    pipenv run python3 classic-enum.py $year
done