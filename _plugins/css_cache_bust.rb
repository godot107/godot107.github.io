# frozen_string_literal: true
#
# Repairs the `bust_css_cache` filter from jekyll-cache-bust (0.0.1), which
# al_folio_core's _includes/head.liquid applies to /assets/css/main.css.
#
# The gem digests the concatenated contents of `assets/_sass/**/*`. al-folio
# kept its partials there back when it was a plain Jekyll site; as a theme gem
# they live in `_sass/`, and this starter ships none of its own. The glob
# therefore matches nothing, the digest is MD5("") —
# d41d8cd98f00b204e9800998ecf8427e — and the token is a constant. Every deploy
# emitted that same value, so main.css was only ever revalidated when its
# max-age (600s) expired, and a CSS change was invisible to a returning visitor
# until then.
#
# main.css is compiled from Sass and so does not exist on disk when head.liquid
# renders, which rules out digesting the output. Digest its inputs instead:
# this site's own stylesheet, any partial directory that is actually readable,
# and the theme version — which stands in for the gem's own partials, since the
# contents of a released version never change.
#
# Reopening the module is enough to take effect: Liquid registered the module
# itself as a filter set, so strainers resolve the method at call time, and
# _plugins/*.rb load after the :jekyll_plugins gems.

require "digest/md5"

module Jekyll
  module CacheBust
    # This site's own stylesheet. `_sass` is the gem's layout, `assets/_sass`
    # the pre-gem one; both are probed so the digest keeps working either way.
    CSS_SOURCE_FILES = ["assets/css/main.scss"].freeze
    CSS_SOURCE_DIRS = ["_sass", "assets/_sass"].freeze

    module_function

    def theme_version
      spec = Gem.loaded_specs["al_folio_core"]
      spec ? "al_folio_core-#{spec.version}" : "al_folio_core-unresolved"
    end

    def css_source_digest
      parts = []

      CSS_SOURCE_FILES.each do |file|
        parts << File.read(file) if File.file?(file)
      end

      CSS_SOURCE_DIRS.each do |dir|
        next unless Dir.exist?(dir)

        # Sorted so the digest does not depend on directory iteration order.
        Dir[File.join(dir, "**", "*")].sort.each do |file|
          parts << File.read(file) if File.file?(file)
        end
      end

      parts << theme_version

      Digest::MD5.hexdigest(parts.join)
    end
  end

  module CacheBust
    def bust_css_cache(file_name)
      [file_name, "?v=", Jekyll::CacheBust.css_source_digest].join
    end
  end
end
