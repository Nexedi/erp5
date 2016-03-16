/* Copyright (c) 2014 Nexedi
 *                    Vincent Pelletier <vincent@nexedi.com>
 *
 * WARNING: This program as such is intended to be used by professional
 * programmers who take the whole responsability of assessing all potential
 * consequences resulting from its eventual inadequacies and bugs
 * End users who are looking for a ready-to-use solution with commercial
 * garantees and support are strongly adviced to contract a Free Software
 * Service Company
 *
 * This program is Free Software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */
/*jslint browser: true, bitwise: true, unparam: true, indent: 2, maxlen: 80 */

function SequenceDetector(sequence, wrap, start, character_score,
    is_lower, is_upper) {
  "use strict";
  this.sequence = sequence;
  this.wrap = wrap;
  this.index = start;
  this.variety = character_score;
  this.has_lower = is_lower;
  this.has_upper = is_upper;
  this.matched = 1;
  this.direction = 0;
}

SequenceDetector.prototype.eq = function (index, character) {
  "use strict";
  if (this.wrap) {
    index %= this.sequence.length;
  }
  return this.sequence.charAt(index) === character;
};

SequenceDetector.prototype.next = function (character, character_score,
    is_lower, is_upper) {
  "use strict";
  if (this.direction === 0) {
    /* second char of the supposed sequence, guess direction */
    if (this.eq(this.index + 1, character)) {
      this.direction = 1;
    } else if (this.eq(this.index - 1,  character)) {
      this.direction = -1;
    } else {
      /* not a sequence */
      return false;
    }
  } else if (!this.eq(this.index + this.direction, character)) {
    /* sequence ended */
    return false;
  }
  this.index += this.direction;
  this.matched += 1;
  this.variety += character_score;
  this.has_lower |= is_lower;
  this.has_upper |= is_upper;
  return true;
};

function SequenceDetectorFactory(sequence, wrap) {
  "use strict";
  this.sequence = sequence;
  this.wrap = wrap;
}

SequenceDetectorFactory.prototype.getDetector = function (character,
    character_score, is_lower, is_upper) {
  "use strict";
  var index = this.sequence.indexOf(character);
  if (index === -1) {
    return null;
  }
  return new SequenceDetector(this.sequence, this.wrap, index, character_score,
    is_lower, is_upper);
};

function PasswordValidator() {
  "use strict";
  /* Double all sequences so crossing sequence boundaries still counts as
   * sequence. */
  var orig_sequences = this.SEQUENCES,
    sequences = [],
    sequence,
    i;
  this.SEQUENCES = sequences;
  for (i = 0; i < orig_sequences.length; i += 1) {
    sequence = orig_sequences[i];
    sequences.push(new SequenceDetectorFactory(sequence[0], sequence[1]));
  }
}
window.PasswordValidator = PasswordValidator;


/* Uniqueness is a reweard for not reusing the same character several times.
 * SCORE_UNIQUE increase this reward, SCORE_UNIQUE_DIVISOR is the divisor
 * used to determine the score of repetitions. */
PasswordValidator.prototype.SCORE_UNIQUE = 1;
/* Obviously:
 * - zero is will cause errors
 * - negative values will give non-linear scores
 * - values between zero and one will reward for repetitions (you do not want
 *   this)
 * - use Infinity to only reward unique chars */
PasswordValidator.prototype.SCORE_UNIQUE_DIVISOR = 1.5;
PasswordValidator.prototype.SCORE_UPPER = 1;
PasswordValidator.prototype.SCORE_LOWER = 1;
/* Password variety is the number of unique chars in it. Score is computed
 * as the variety elevated to the power of SCORE_VARIETY, and added to
 * password score. */
PasswordValidator.prototype.SCORE_VARIETY = 2;
/* Sequences are SEQUENCE_THRESHOLD or more consecutive chars in password which
 * are in direct or reverse order of any of SEQUENCES. */
PasswordValidator.prototype.SEQUENCE_THRESHOLD = 3;
PasswordValidator.prototype.SEQUENCES = [
  ["abcdefghijklmnopqrstuvwxyz", true],
  ["0123456789", true],
  /* azerty */
  ["azertyuiop", false],
  ["qsdfghjklm", false],
  ["wxcvbn", false],
  /* qwerty */
  ["qwertyuiop", false],
  ["asdfghjkl", false],
  ["zxcvbnm", false],
  /* qwertz */
  ["qwertzuiop", false],
  ["yxcvbnm", false]
];
/* Classes are types of characters. Password should contain chars from as
 * many classes as possible. Score is computed as the number of found class
 * elevated to the power of SCORE_CLASS, and added to password score.
 * Upper and lower case are treated separately, but are handled as classes. */
PasswordValidator.prototype.SCORE_CLASS = 3;
PasswordValidator.prototype.CLASSES = [
  /\d/,
  /\W/
];
/* Padding is appended to password internally for code simplicity. It must not
 * be present in any provided password. The null character seems like a
 * reasonable choice. */
PasswordValidator.prototype.PADDING = "\x00";

/* Ranges have a low threshold, CSS-friendly name, and human-readable caption.
 */
/* Weakest password range name. */
PasswordValidator.prototype.RANGE_BASE = "too-weak";
/* Above-weakest range definition, as threshold and range name pairs. */
PasswordValidator.prototype.RANGE_THRESHOLDS = [
  [54, "weak"],
  [70, "medium"],
  [90, "strong"]
];
/* Range name to human-friendly caption mapping. Override for l10n. */
PasswordValidator.prototype.RANGE_CAPTION = {
  "too-weak": "Too weak",
  "weak": "Weak",
  "medium": "Medium",
  "strong": "Strong"
};
/* Ignore given sequences when wholy found in a password. Unlike SEQUENCES,
 * BLACKLIST entries are char-order-sensitive. Some entries come from the 2013
 * top-25 most common passwords, ignoring those already getting a poor score
 * from other criterions. */
PasswordValidator.prototype.BLACKLIST = [
  "password",
  "iloveyou",
  "admin",
  "letmein",
  "monkey",
  "sunshine",
  "shadow",
  "princess",
  "trustno1"
];

PasswordValidator.prototype.getScoreRange = function (score) {
  "use strict";
  var range = this.RANGE_BASE, i;
  for (i = 0; i < this.RANGE_THRESHOLDS.length; i += 1) {
    if (score < this.RANGE_THRESHOLDS[i][0]) {
      break;
    }
    range = this.RANGE_THRESHOLDS[i][1];
  }
  return range;
};

PasswordValidator.prototype.getScore = function (value, tracer) {
  "use strict";
  var variety = 0,
    variety_map = {},
    padded_value,
    lower,
    upper,
    is_lower,
    is_upper,
    has_lower = 0,
    has_upper = 0,
    sequences = [],
    new_sequences,
    sequence_matched,
    sequence = null,
    current_value,
    current_lower,
    value_index,
    character_score,
    class_count = 0,
    class_index,
    current_substring,
    current_blacklist,
    class_pattern,
    lazy_tracer,
    i;
  variety_map[this.PADDING] = 0;
  if (tracer === undefined) {
    lazy_tracer = function () {};
  } else {
    lazy_tracer = function () {
      /* concatenate message, to reduce cost when tracer is undefined */
      var offset = arguments[0],
        message = arguments[1],
        i;
      for (i = 2; i < arguments.length; i += 1) {
        message += arguments[i];
      }
      tracer(offset, message);
    };
  }
  if (value.indexOf(this.PADDING) !== -1) {
    throw "input contains padding char";
  }
  padded_value = value + this.PADDING;
  upper = padded_value.toLocaleUpperCase();
  lower = padded_value.toLocaleLowerCase();
  for (value_index = 0; value_index < padded_value.length; value_index += 1) {
    current_substring = lower.substr(value_index);
    for (i = 0; i < this.BLACKLIST.length; i += 1) {
      current_blacklist = this.BLACKLIST[i];
      if (current_substring.substr(0, current_blacklist.length
          ) === current_blacklist) {
        value_index += current_blacklist.length;
        break;
      }
    }
    current_value = padded_value.charAt(value_index);
    current_lower = lower.charAt(value_index);
    is_lower = current_value !== upper.charAt(value_index) &&
               current_value === lower.charAt(value_index);
    is_upper = current_value !== lower.charAt(value_index) &&
               current_value === upper.charAt(value_index);
    character_score = variety_map[current_lower];
    if (character_score === undefined) {
      character_score = this.SCORE_UNIQUE;
    }
    lazy_tracer(value_index, "variety:", character_score);
    variety_map[current_lower] = character_score / this.SCORE_UNIQUE_DIVISOR;
    new_sequences = [];
    sequence_matched = false;
    for (i = 0; i < sequences.length; i += 1) {
      sequence = sequences[i];
      if (sequence.next(current_lower, character_score, is_lower, is_upper)) {
        lazy_tracer(value_index, "sequence still matching ", sequence.sequence,
          " at ", sequence.index, " going ", sequence.direction);
        new_sequences.push(sequence);
      /* First sequence is always the longest match known yet. This is an
       * imperfect way of choosing the sequence which eats most chars, but it
       * should be sufficiently close to best result.
       * Exemple of it going wrong:
       *   password = "12345";
       *   SEQUENCES = [["123", false], ["2345", false]];
       * First sequence will match for 3 chars, and second will get discarded
       * although it could have eaten 4.
       * Likewise for
       *   SEQUENCES = [["123", false], ["1234", false]];
       * so overall it's mostly a matter of which sequences are defined and in
       * which order.
       */
      } else if (i === 0 &&
          sequence.matched >= this.SEQUENCE_THRESHOLD) {
        lazy_tracer(value_index, "sequence done matching ", sequence.sequence);
        sequence_matched = true;
        /* matching sequences count as a single neither upper- nor lower-case,
         * unique character. That latest caracteristic is too laxist, but
         * costly to verify. */
        variety += 1;
        new_sequences = [];
        break;
      }
    }
    if (!sequence_matched && sequences.length !== 0 && (
        new_sequences.length === 0 || (
          new_sequences[0].matched <= sequences[0].matched &&
          new_sequences[0] !== sequences[0]
        )
      )) {
      /* Best candidates all ended */
      sequence = sequences[0];
      lazy_tracer(value_index,
        "sequence best candidates failed matching, accepting variety:",
        sequence.variety, " lower:", sequence.has_lower,
        " upper:", sequence.has_upper);
      variety += sequence.variety;
      has_lower |= sequence.has_lower;
      has_upper |= sequence.has_upper;
      new_sequences = [];
    }
    sequences = new_sequences;
    for (i = 0; i < this.SEQUENCES.length; i += 1) {
      sequence = this.SEQUENCES[i].getDetector(current_lower, character_score,
        is_lower, is_upper);
      if (sequence !== null) {
        lazy_tracer(value_index, "sequence candidate ", sequence.sequence,
          " at ", sequence.index);
        sequences.push(sequence);
      }
    }
    if (sequences.length === 0) {
      lazy_tracer(value_index,
        "no matching sequence, accepting variety:", character_score,
        " lower:", is_lower, " upper:", is_upper);
      variety += character_score;
      has_lower |= is_lower;
      has_upper |= is_upper;
    }
  }
  if (has_lower) {
    lazy_tracer(value_index, "has lower");
    class_count += this.SCORE_LOWER;
  }
  if (has_upper) {
    lazy_tracer(value_index, "has upper");
    class_count += this.SCORE_UPPER;
  }
  for (class_index = 0; class_index < this.CLASSES.length; class_index += 1) {
    class_pattern = this.CLASSES[class_index];
    if (value.match(class_pattern)) {
      lazy_tracer(value_index, "matches ", class_pattern);
      class_count += 1;
    }
  }
  return Math.pow(variety, this.SCORE_VARIETY) +
         Math.pow(class_count, this.SCORE_CLASS);
};

if ($.hasOwnProperty("validator")) {
  $.validator.addMethod("passwordMetter", function (value, element, params) {
    "use strict";
    var metter,
      /* use untrimmed value */
      password = element.value,
      optional = this.optional(element),
      validator = params.validator,
      score,
      range,
      score_percent,
      parent;
    if (params.hasOwnProperty("metter")) {
      metter = params.metter;
    } else {
      parent = $(element).parent();
      parent.append('<div class="password-meter" style="display:none"><div class="password-meter-message"></div><div class="password-meter-bg"><div class="password-meter-bar"></div></div></div>');
      params.metter = metter = parent.find(".password-meter");
    }
    metter.hide();
    if (!optional || password.length) {
      score = validator.getScore(password);
      range = validator.getScoreRange(score);
      score_percent = Math.round(Math.min(1,
        score / validator.RANGE_THRESHOLDS[validator.RANGE_THRESHOLDS.length - 1
          ][0]) * 100);
      metter.find(".password-meter-bar")
        .removeClass()
        .addClass("password-meter-bar")
        .addClass("password-meter-" + range)
        .width(score_percent + "%");
      metter.find(".password-meter-message")
        .removeClass()
        .addClass("password-meter-message")
        .addClass("password-meter-message-" + range)
        .text(validator.RANGE_CAPTION[range]);
      metter.show();
      return range !== validator.RANGE_BASE;
    }
    return optional;
  }, "");
}