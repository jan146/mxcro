from serverless.get_daily_rda import main

if __name__ == "__main__":
    args: dict[str, str] = {
        "gender": "m",
        "weight": "80",
        "height": "185",
        "age": "28",
        "activity_level": "light",
    }
    result = main(args)
    print(result)
