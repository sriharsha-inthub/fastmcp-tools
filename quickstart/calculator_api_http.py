from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel


app = FastAPI(
    title="FastAPI MCP Calculator",
    description="A simple calculator MCP that performs basic arithmetic operations using FastAPI.",
    version="1.0.0"
    )

@app.get("/about")
def about() -> dict:
    return {
                "version": "1.0.0", 
                "name": "FastAPI MCP Calculator", 
                "description": "A simple calculator MCP that performs basic arithmetic operations using FastAPI.",
                "tools": ["addition", "subtract", "multiply", "divide", "reminder"]
            }


class Numbers(BaseModel):
    name: str
    description: str | None = None
    first_number: float = 0
    second_number: float = 0

class DividentDivisor(BaseModel):
    name: str
    description: str | None = None
    dividend: float = 0
    divisor: float = 1

@app.get("/addition")
def addition(first_number: float = 0, second_number: float = 0) -> dict:
    """
    Add two numbers & return the sum.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The sum of the two numbers.
    
    """
    sum = first_number + second_number
    return { "result": sum }

@app.get("/subtract")
def substract(first_number: float = 0, second_number: float = 0) -> dict:
    """
    Substract two numbers & return the difference.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The difference of the two numbers.
    
    """
    diff = first_number - second_number
    return { "result": diff }

@app.get("/multiply")
def multiply(first_number: float = 0, second_number: float = 0) -> dict:
    """
    Multiply two numbers & return the product.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The Product of two numbers.
    
    """
    product = first_number * second_number
    return { "result": product }

@app.get("/divide")
def divide(dividend: float = 0, divisor: float = 0) -> dict:
    """
    Divide two numbers & return the quotient.
    
    args:
        dividend (float): The first number.
        divisor (float): The second number.        
    returns:
        float: The quotient of two numbers.
    
    """
    if divisor == 0:
        return { "error": "Division by zero is not allowed." }
    quotient = dividend * divisor
    return { "result": quotient }

@app.get("/reminder")
def reminder(dividend: float = 0, divisor: float = 0) -> dict:
    """
    Divide two numbers & return the reminder.
    
    args:
        dividend (float): The first number.
        divisor (float): The second number.        
    returns:
        float: The reminder of two numbers.
    
    """
    if divisor == 0:
        return { "error": "Division by zero is not allowed." }
    reminder = dividend * divisor
    return { "result": reminder }

@app.post("/addition")
def addition(numbers: Numbers = Numbers (name="addition", description="Add two numbers", first_number=0, second_number=0)) -> dict:
    """
    Add two numbers & return the sum.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.
    returns:
        float: The sum of the two numbers.
    
    """
    sum = numbers.first_number + numbers.second_number
    return { "result": sum }

@app.post("/subtract")
def substract(numbers: Numbers = Numbers (name="subtract", description="Subtract two numbers", first_number=0, second_number=0)) -> dict:
    """
    Substract two numbers & return the difference.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The difference of the two numbers.
    
    """
    diff = numbers.first_number - numbers.second_number
    return { "result": diff }

@app.post("/multiply")
def multiply(numbers: Numbers = Numbers (name="multiply", description="Multiply two numbers", first_number=0, second_number=0)) -> dict:
    """
    Multiply two numbers & return the product.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The Product of two numbers.
    
    """
    product = numbers.first_number * numbers.second_number
    return { "result": product }

@app.post("/divide")
def divide(numbers: DividentDivisor = Numbers (name="divide", description="Divide two numbers and get the quotient", dividend=0, divisor=0 )) -> dict:
    """
    Divide two numbers & return the quotient.
    
    args:
        dividend (float): The first number.
        divisor (float): The second number.        
    returns:
        float: The quotient of two numbers.
    
    """
    if numbers.divisor == 0:
        return { "error": "Division by zero is not allowed." }
    quotient = numbers.dividend * numbers.divisor
    return { "result": quotient }

@app.post("/reminder")
def reminder(numbers: DividentDivisor = Numbers (name="reminder", description="Divide two numbers and get the reminder", dividend=0, divisor=0 )) -> dict:
    """
    Divide two numbers & return the reminder.
    
    args:
        dividend (float): The first number.
        divisor (float): The second number.        
    returns:
        float: The reminder of two numbers.
    
    """
    if numbers.divisor == 0:
        return { "error": "Division by zero is not allowed." }
    reminder = numbers.dividend * numbers.divisor
    return { "result": reminder }

# converting to mcp server
mcp = FastApiMCP(
        app,
        name="FastAPI MCP Calculator",
        description="A simple calculator MCP that performs basic arithmetic operations using FastAPI.",
    )
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn 
    # runs fast api server
    uvicorn.run(app, host="localhost", port=8100)

