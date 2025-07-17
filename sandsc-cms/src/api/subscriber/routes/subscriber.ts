export default {
  routes: [
    {
      method: 'POST',
      path: '/subscribers',
      handler: 'subscriber.create',
      config: {
        policies: [],
        middlewares: [],
      },
    },
  ],
};
