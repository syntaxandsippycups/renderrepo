import type { Lifecycle } from '@strapi/strapi';

export default {
  async afterCreate(event) {
    const { result } = event;

    // Fetch all subscribers
    const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber', {
      fields: ['email'],
    });

    // Send an email to each subscriber
    for (const subscriber of subscribers) {
      try {
        await strapi.plugin('email').service('email').send({
          to: subscriber.email,
          subject: `New Blog Post: ${result.Title}`,
          html: `<h1>${result.Title}</h1>
                 <p>${result.content?.slice(0, 150)}...</p>
                 <p><a href="https://syntaxandsippycups.com/blog/${result.slug}">Read more</a></p>`,
        });
      } catch (err) {
        strapi.log.error(`Failed to email ${subscriber.email}: ${err}`);
      }
    }
  },
} satisfies Lifecycle;
