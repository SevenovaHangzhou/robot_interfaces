# Measured feedback of one swerve wheel (member of WheelObservationArray). Values come from
# hardware feedback only, never from command targets or fused chassis velocity.

uint8 FRONT_LEFT=0
uint8 FRONT_RIGHT=1
uint8 REAR_LEFT=2
uint8 REAR_RIGHT=3
uint8 wheel_id

# Calibrated steering-axis position in the array's header.frame_id, metres. The
# steering-axis-to-contact-patch offset is not included.
float64 steering_axis_x
float64 steering_axis_y
# Effective rolling radius used by RT-Control odometry, metres.
float64 wheel_radius

# Wheel-axis accumulated angle, rad, reduction and sign applied. Its origin is arbitrary;
# use differences within one epoch only.
float64 drive_position
# Wheel-axis angular velocity, rad/s, as measured by the drive. Positive rolls the wheel
# along the steering angle.
float64 drive_velocity
WheelFeedbackChannel drive

# Steering angles: heading of the positive rolling direction from +x of header.frame_id,
# counter-clockwise positive, in the calibrated mechanical-travel coordinate (no wrapping,
# no pi branch switch). The two sources are kept separate and are not independent.
# Derived from the steering motor feedback.
float64 steering_motor_angle
WheelFeedbackChannel steering_motor
# Measured by the external steering encoder.
float64 steering_encoder_angle
WheelFeedbackChannel steering_encoder
