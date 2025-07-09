declare module "*.module.css" {
  const classes: { [key: string]: string };
  export default classes;
}

declare module "*.mp4" {
  const src: string;
  export default src;
}