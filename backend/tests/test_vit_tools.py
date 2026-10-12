from app.agent.tools.vit_tools import AttendanceCalculatorTool, CGPACalculatorTool

def test_attendance_tool():
    tool = AttendanceCalculatorTool()
    
    # Normal target
    res = tool.execute(current_attended=38, current_total=45, target_percentage=75.0)
    assert res["current_percentage"] >= 84.4
    assert res["classes_needed"] == 0
    
    # 0 classes
    res = tool.execute(current_attended=0, current_total=0)
    assert "error" in res
    
    # Need classes
    res = tool.execute(current_attended=10, current_total=20, target_percentage=75.0)
    assert res["classes_needed"] == 20
    
    # Impossible? Math allows unbounded classes to catch up.
    
def test_cgpa_tool():
    tool = CGPACalculatorTool()
    
    res = tool.execute(grades=["S", "A", "B"], credits=[4, 3, 3])
    # 10*4 + 9*3 + 8*3 = 40 + 27 + 24 = 91
    # total credits = 10
    assert res["sgpa"] == 9.1
    
    # Length mismatch
    res = tool.execute(grades=["S", "A"], credits=[4, 3, 3])
    assert "error" in res
