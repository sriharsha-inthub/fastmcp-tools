from fastmcp import FastMCP, Context

mcp = FastMCP(
    name="Simple Calculator Stdio",
    version="1.0.0",    
    tools=[],
    auth=None, # OAuthProvider \ TokenVerifier
)


@mcp.resource(
        uri="about://calculator",
        name="about_calculator", 
        tags=["about", "calculator"], 
        enabled=True
    )
async def about(ctx: Context) -> dict:
    """
    Privides information about this calculator MCP.
    
    returns:
        str: Information about this calculator MCP.
    
    """
    await ctx.debug("about_calculator resource called.")
    print("about://calculator resource called.")
    return  {
                "version": "1.0.0", 
                "name": "Simple Calculator Stdio", 
                "description": "A simple calculator MCP that performs basic arithmetic operations.",
                "tools": ["addition", "subtract", "multiply", "divide", "reminder"]
            }

@mcp.tool()
def addition(first_number: float, second_number: float, ctx: Context) -> float:
    """
    Add two numbers.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The sum of the two numbers.
    
    """
    ctx.debug("addition::tool called.")
    print("addition::tool called.")
    sum = first_number + second_number
    ctx.info(f"Calculated sum: {sum}")
    return sum

@mcp.tool(
    name="subtract",
    tags=["math", "arithmetic", "subtraction"],
    enabled=True
)
def subtract(first_number: float, second_number: float, ctx: Context) -> float:
    """
    Subtract two numbers.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The difference of the two numbers.
    
    """
    ctx.debug("caculator::subtract::tool called.")
    print("caculator::subtract::tool called.")
    diff = first_number - second_number
    ctx.info(f"Calculated difference: {diff}")
    return diff

@mcp.tool(
    name="multiply",
    tags=["math", "arithmetic", "multiplication"],
    enabled=True
)
def multiply(first_number: float, second_number: float, ctx: Context) -> float:
    """
    Multiply two numbers.
    
    args:
        first_number (float): The first number.
        second_number (float): The second number.        
    returns:
        float: The product of the two numbers.
    
    """
    ctx.debug("caculator::multiply::tool called.")
    print("caculator::multiply::tool called.")
    product = first_number * second_number
    ctx.info(f"Calculated product: {product}")
    return product

@mcp.tool(
    name="divide",
    tags=["math", "arithmetic", "division"],
    enabled=True
)
def divide(dividend: float, divisor: float, ctx: Context) -> float:
    """
    Multiply two numbers.
    
    args:
        dividend (float): The first number.
        divisor (float): The second number.        
    returns:
        float: The quotient of the two numbers.
    
    """
    ctx.debug("caculator::divide::tool called.")
    print("caculator::divide::tool called.")
    if divisor == 0:
        raise ValueError("Cannot divide by zero(divisor).")
    quotient = dividend / divisor
    ctx.info(f"Calculated quotient: {quotient}")
    return quotient

@mcp.tool(
    name="reminder",
    tags=["math", "arithmetic", "reminder"],
    enabled=True
)
def reminder(dividend: float, divisor: float, ctx: Context) -> float:
    """
    Divide two numbers & get the reminder.
    
    args:
        dividend (float): The first number.
        divisor (float): The second number.        
    returns:
        float: The reminder of the two numbers.
    
    """
    ctx.debug("caculator::reminder::tool called.")
    print("caculator::reminder::tool called.")
    if divisor == 0:
        raise ValueError("Cannot divide by zero(divisor).")
    reminder = dividend % divisor
    ctx.info(f"Calculated reminder: {reminder}")
    return reminder

if __name__ == "__main__":
    mcp.run(transport="stdio") # stdio by default
    #mcp.run(transport="http", host="localhost", port=8009, show_banner=False)