
import { sendNewPostEmail } from '../../../utils/email';

export default {
  async afterCreate(event: any) {
    const { result } = event;

    // Get all subscribers
    const subscribers = await strapi.entityService.findMany('api::subscriber.subscriber', {
      fields: ['email'],
    });

    for (const sub of subscribers) {
      if (sub.email) {
        await sendNewPostEmail(sub.email, result.title);
      }
    }
  },
};
