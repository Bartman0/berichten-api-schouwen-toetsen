const jsonServer = require("json-server");
const server = jsonServer.create();
const router = jsonServer.router("db.json");
const middlewares = jsonServer.defaults();

// In this example we simulate a server side error response
router.render = (req, res) => {
  res.status(201).jsonp(res.locals.data);
};

function isAuthorized(req) {
  const authHeader = req.headers["authorization"];
  return authHeader;
}

server.use(middlewares);
server.use((req, res, next) => {
  if (isAuthorized(req)) {
    // add your authorization logic here
    next(); // continue to JSON Server router
  } else {
    res.sendStatus(401);
  }
});
server.use(router);
server.listen(3000, () => {
  console.log("JSON Server is running");
});
