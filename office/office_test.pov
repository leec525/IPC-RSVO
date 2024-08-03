#include "colors.inc"
#include "stones.inc"

#declare office_height=300;
camera{
  right x*image_width/image_height
  angle 90
  rotate<rotx,roty,rotz>
  translate<transx,transy,transz>
  /* direction 2.8*z */
 translate office_height*y
}

box{
  <500,230,-500>,<-500,241,500>
  texture{pigment{color Red}}
  translate office_height*y
}
box{
  <500,10,-500>,<-500,21,500>
  texture{pigment{color Orange}}
  translate office_height*y
}
box{
  <500,-500,280>,<-500,500,300>
  texture{pigment{color Orange}}
  translate office_height*y
}
box{
  <500,-500,30>,<-500,500,50>
  texture{pigment{color Blue}}
  translate office_height*y
}
sphere {
  <0,128,120>,5.0
  translate office_height*y
  /* translate room_width*x */
  /* translate room_length*z */
texture{
pigment{color Red}
}
}
sphere {
  <0,138,116>,5.0
  translate office_height*y
  /* translate room_width*x */
  /* translate room_length*z */
texture{
pigment{color Green}
}
}
box {
  <0,135,116>,<11,165,120>
  translate office_height*y
  /* translate room_width*x */
  /* translate room_length*z */
texture{
pigment{color Yellow}
}
}
light_source{
  // placed at the origin
  <0,108 110>

  // obtain color+intensity
  color White
  /* color <0.3,0.3,0.3>//一半的强度的白光 */
  // area light?面光源渲染好像有点慢
  /* area_light <8,0,0>,<0,0,8>,20,20 */
  // realistic fading 这里可能引起每次渲染不一样
  /* fade_distance 2*pi*10
  fade_power 2 */
  translate (office_height-50)*y
}
