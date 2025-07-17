export default {
  routes: [
    {
      method: 'POST',
      path: '/subscribers',
      handler: 'subscriber.create',
      config: {
        auth: false, // or true if you want it protected
        policies: [],
        middlewares: [],
      },
    },
  ],
};
