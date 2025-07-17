import { sendNewPostEmail } from '../../../utils/email';

export default {
  async afterCreate(event) {
    const { result } = event;

    const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber', {
      fields: ['email'],
    });

    for (const sub of subscribers) {
      await sendNewPostEmail(sub.email, result.title);
    }
  },
};
