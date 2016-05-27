import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.route('viewannotation');
  this.route('editannotation');
  this.route('diseaseconcepts');
});

export default Router;
