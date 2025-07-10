# PIDController class build from sources by https://medium.com/@aleksej.gudkov/python-pid-controller-example-a-complete-guide-5f35589eec86

class PIDController:
    def __init__(self, Kp: float, Ki: float, Kd: float):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prevError = 0
        self.integral = 0
        
    def calculate(self, setpoint: float, current_position: float, dt: float) -> float:
        error = setpoint - current_position
        
        P_out = self.Kp * error
        
        self.integral += error * dt
        I_out = self.Ki * self.integral
        
        derivative = (error - self.prevError) / dt
        D_out = self.Kd * derivative
        
        self.previous_error = error
        
        return P_out + I_out + D_out