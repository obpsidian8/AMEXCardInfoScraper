def logger(msg, status="INFO"):
    if status == "ERROR":
        prefix = "\u001b[31mLOG ERROR: "
    elif status == "SUCCESS":
        prefix = "\u001b[32mLOG SUCCESS: "
    elif status == "WARNING":
        prefix = "\u001b[33mLOG WARNING: "
    else:
        prefix = "\u001b[34mLOG INFO: "

    print(f"{prefix}{msg}\u001b[0m")
