#include <boost/python.hpp>
#include <string>


#include <iostream>
#include <ctime>
#include <cstdio>
using namespace std;

namespace py = boost::python;
// #pragma once


class PID {
public:
  float last_error;
  float output;
  float SetPoint;
  float Kp ,  Ti ,  Td , Ki , Kd;
  float integral;
  float interval;
  float error_threshold;
  float output_upper_limit;
  float output_lower_limit;
  float error;
  float PTerm , ITerm , DTerm  , int_error , windup_guard , windup_limit;
  time_t   current_time , last_time ;
  float sample_time;


public:
  /// Public constructor
  PID()
  {}

  PID(float P , float I ,  float D )
  {
    Kp = P; Ki = I; Kd = D;
    //sample_time = 0;
    current_time = time(NULL);
    last_time = current_time;
    SetPoint = 0;

    //int_error = 0;
    windup_guard = 100000;
    windup_limit = 10000;

    output = 0;
    clear();
  }

  py::list get_PID();

  void set_PID(float P , float I ,  float D )
  {
    Kp = P; Ki = I; Kd = D;
    //sample_time = 0;
    current_time = time(NULL);
    last_time = current_time;
    SetPoint = 0;

    //int_error = 0;
    windup_guard = 100000;
    windup_limit = 10000;

    output = 0;
    clear();
  }
  void clear()
  {

    PTerm = 0;
    ITerm = 0;
    DTerm = 0;
    last_error = 0;

  }

  /// Set the proportional term. Use it AFTER setupdateInterval or setupdateRate
  void setKp(const float &Kp);

  /// Set the integral term. Use it AFTER setupdateInterval or setupdateRate
  void setTi(const float &Ti);

  /// Set the derivative term. Use it AFTER setupdateInterval or setupdateRate
  void setTd(const float &Td);

  void setKi(const float &Ki);

  /// Set the derivative term. Use it AFTER setupdateInterval or setupdateRate
  void setKd(const float &Kd);

  /// Set the P ,  I ,  D terms respectively. Use it AFTER setupdateInterval or setupdateRate
  void setWeights(const float &Kp ,  const float &Ki ,  const float &Kd);

  /// Set the update interval of the controller in seconds.
  /// If you don't know the interval you can set the frequency of update using setupdateRate
  void setupdateInterval(const float &update_interval);

  /// Set the update frequency of the controller in hertz.
  /// If you don't know the update frequency you can set the update interval using setupdateRate
  void setupdateRate(const float &update_rate);

  /// Set the minimun error for computation of the PID loop. The default is 0.0
  /// It can be set to prevent integral windup or updates with minimal errors
  void setErrorThreshold(const float &error_threshold);

  /// Set the lower limit of the output. Output will be clamped to this value.
  /// If clamped ,  the integral will not be computed to prevent integral windup.
  /// To set the upper limit use setOutputUpperLimit
  /// YOU NEED TO SET IT!
  void setwindup_guard(const float &output_lower_limit);

  /// Set the upper limit of the output. Output will be clamped to this value.
  /// If clamped ,  the integral will not be computed to prevent integral windup.
  /// To set the lower limit use setOutputLowerLimit
  /// YOU NEED TO SET IT!
  void setwindup_limit(const float &output_upper_limit);

  /// Set the desired point of the output.
  /// This is the output the PID loop will try to reach.
  /// error will be computed subtracting the feedback input from this value
  void setDesiredPoint(const float &desired_point);
  float getDesiredPoint()
  {
    return SetPoint;
  }

  /// The update funcion that make all the PID computation.
  /// Call it at specific rate ,  setted by setupdateRate or setupdateInterval (read descriptions).
  /// (use a timer interrupt if used on a embedded microcontroller)
  /// The feedback_input is the value from the feedback.
  /// The returned value is the output value of the filter.
  float update(const float &feedback_input);
};


py::list PID::get_PID()
{
    py::list para;
    para.append(Kp);
    para.append(Ki);
    para.append(Kd);
    return para;
}

void PID::setKp(const float &Kp) {
  this->Kp  =  Kp;
}

void PID::setTi(const float &Ti) {
  this->Ti  =  Ti;
}

void PID::setTd(const float &Td) {
  this->Td  =  Td;
}
void PID::setKi(const float &Ki) {
  this->Ki  =  Ki;
}

void PID::setKd(const float &Kd) {
  this->Kd  =  Kd;
}

void PID::setWeights(const float &Kp ,  const float &Ki ,  const float &Kd) {
  setKp(Kp);
  setKi(Ki);
  setKd(Kd);
}

void PID::setupdateInterval(const float &update_interval) {
  interval  =  update_interval;
}

void PID::setupdateRate(const float &update_rate) {
  interval  =  1.f / update_rate;
}

void PID::setErrorThreshold(const float &error_threshold) {
  this->error_threshold  =  error_threshold;
}

void PID::setwindup_limit(const float &output_lower_limit) {
  this->windup_limit  =  output_lower_limit;
}

void PID::setwindup_guard(const float &output_upper_limit) {
  this->windup_guard  =  output_upper_limit;
}

void PID::setDesiredPoint(const float &desired_point) {

  SetPoint  =  desired_point;
  std::cout << "desiredP" << SetPoint << std::endl;
}

float PID::update(const float &feedback_input) {
  error  =  feedback_input;
  printf("in update %f\n", error);
  // if(error>180) error = error-360;
  // if(error<-180) error =error+360;
  //if(fabs(error)<0.5) error=0;
  current_time = time(NULL);
  float delta_time = (current_time - last_time);
  float delta_error = error - last_error;
  if (delta_time >= sample_time)
  {
    PTerm = Kp * error;
    ITerm += error * delta_time;
    DTerm = 0;
    if (delta_time > 0)
      DTerm = delta_error / delta_time;

    if (ITerm < -windup_guard) ITerm = -windup_guard;
    else if (ITerm > windup_guard) ITerm = windup_guard;

    last_time = current_time;
    last_error = error;
    //if(fabs(error)>45) ITerm=0;
    output = PTerm + Ki * ITerm + Kd * DTerm;

    if (output < -windup_limit) output = -windup_limit;
    else if (output > windup_limit) output = windup_limit;
    //last_output= output;
    return output;
  }
  return output;
}


BOOST_PYTHON_MODULE(PID){
    py::class_<PID>("PID", py::init<>())
        .def(py::init<float,float,float>())
        .def("set_PID", &PID::set_PID)
        .def("get_PID", &PID::get_PID)
        .def("clear", &PID::clear)
        .def("setKp", &PID::setKp)
        .def("setTi", &PID::setTi)
        .def("setTd", &PID::setTd)
        .def("setKi", &PID::setKi)
        .def("setKd", &PID::setKd)
        .def("setWeights", &PID::setWeights)
        .def("setupdateInterval", &PID::setupdateInterval)
        .def("setupdateRate", &PID::setupdateRate)
        .def("setErrorThreshold", &PID::setErrorThreshold)
        .def("setwindup_limit", &PID::setwindup_limit)
        .def("setwindup_guard", &PID::setwindup_guard)
        .def("setDesiredPoint", &PID::setDesiredPoint)
        .def("getDesiredPoint", &PID::getDesiredPoint)
        .def("update", &PID::update)
        .def_readwrite("last_error", &PID::last_error)
        .def_readwrite("output", &PID::output)
        .def_readwrite("SetPoint", &PID::SetPoint)
        .def_readwrite("Kp", &PID::Kp)
        .def_readwrite("Ti", &PID::Ti)
        .def_readwrite("Td", &PID::Td)
        .def_readwrite("Ki", &PID::Ki)
        .def_readwrite("Kd", &PID::Kd)
        .def_readwrite("integral", &PID::integral)
        .def_readwrite("interval", &PID::interval)
        .def_readwrite("error_threshold", &PID::error_threshold)
        .def_readwrite("output_upper_limit", &PID::output_upper_limit)
        .def_readwrite("output_lower_limit", &PID::output_lower_limit)
        .def_readwrite("error", &PID::error)
        .def_readwrite("PTerm", &PID::PTerm)
        .def_readwrite("ITerm", &PID::ITerm)
        .def_readwrite("DTerm", &PID::DTerm)
        .def_readwrite("int_error", &PID::int_error)
        .def_readwrite("windup_guard", &PID::windup_guard)
        .def_readwrite("windup_limit", &PID::windup_limit)
        .def_readwrite("current_time", &PID::current_time)
        .def_readwrite("last_time", &PID::last_time)
        .def_readwrite("sample_time", &PID::sample_time);  
}


 