import { Hono } from "hono";
import { stream } from "hono/streaming";

// https://hono.dev/getting-started/cloudflare-workers#bindings
type Bindings = {
  MY_BUCKET: R2Bucket;
  USERNAME: string;
  PASSWORD: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.get("/imgs/:username/:step", async (c, next) => {
  const key = `${c.req.param("username")}/${c.req.param("step")}`;
  console.log(`key: ${key}`);
  const res = await c.env.MY_BUCKET.get(key);
  if (res) {
    c.header("Content-Type", "image/png");
    // https://hono.dev/helpers/streaming
    return stream(c, async (s) => {
      s.pipe(res.body);
    });
  } else {
    return c.notFound();
  }
});

app.get("/", (c) => {
  return c.text("Hello Hono!");
});

export default app;
