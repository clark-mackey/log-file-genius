from api.receipt import display_amount
assert display_amount(125) == 125, "minor units must remain integer"
print("amount check passed")
