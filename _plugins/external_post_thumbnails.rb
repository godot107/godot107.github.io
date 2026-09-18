# frozen_string_literal: true
#
# Post-processes blog posts imported from external RSS feeds (Medium, via
# al-folio's `external_sources` in _config.yml). Two automatic jobs that apply
# to every current and future import — no per-post editing required:
#
#   1. De-duplicate. Workflow is: write the post here first, then import it into
#      Medium, whose feed renders it back into the site. So a Medium import that
#      shares a title with a native post in _posts/ is a duplicate — drop it and
#      let the richer, self-hosted native post win.
#
#   2. Thumbnails. The importer doesn't set a preview image, so Medium posts show
#      as text-only cards. Infer a thumbnail from the article's first inline image
#      (the Medium hero) and hotlink it from Medium's CDN.
#
# Runs at :low priority so it executes AFTER the core importer has added the
# external posts to site.posts. The production build uses `bundle exec jekyll
# build` (no --safe), so _plugins/*.rb is loaded.

require "set"

module ExternalPostThumbnails
  # Category that al-folio assigns to external_sources posts (see _config.yml).
  EXTERNAL_CATEGORY = "external-posts"

  module_function

  # Lowercase, unify unicode dashes, strip punctuation/quotes so that titles
  # survive the round-trip through Medium (e.g. "—" vs "-", smart quotes).
  def normalize_title(title)
    title.to_s
         .downcase
         .gsub(/[‐-―]/, "-") # unicode hyphens/dashes -> "-"
         .gsub(/[^a-z0-9]+/, " ")      # drop punctuation, quotes, emoji
         .strip
  end

  # Medium appends " | <site title>" to some imported titles (e.g. "…to finally
  # understand DNS | Willie Man"), which defeats the exact title match in job 1
  # and lets the duplicate through. Strip exactly that suffix, built from the
  # site's own title, so a post whose title merely happens to contain a pipe is
  # left alone.
  def site_byline(site)
    configured = site.config["title"].to_s.strip
    return configured unless configured.empty?

    [site.config["first_name"], site.config["last_name"]].compact.join(" ").strip
  end

  def strip_byline(title, byline)
    return title.to_s if byline.to_s.strip.empty?

    title.to_s.sub(/\s*\|\s*#{Regexp.escape(byline.strip)}\s*\z/i, "")
  end

  # Comparison key for the de-duplication match: byline stripped, then normalized.
  def title_key(title, byline)
    normalize_title(strip_byline(title, byline))
  end

  def external?(doc)
    Array(doc.data["categories"]).map(&:to_s).include?(EXTERNAL_CATEGORY)
  end

  # The hero image is the first inline image in the article body. Skip Medium's
  # invisible tracking pixel (`/_/stat`) and embed players (YouTube/embedly),
  # emoji and avatars; then prefer a real Medium-hosted content image, falling
  # back to any image that at least has a real extension.
  def first_image(content)
    return nil if content.nil? || content.empty?

    srcs = content.scan(/<img[^>]+src=["']([^"']+)["']/i).flatten.reject do |s|
      s.include?("/stat?") || s.include?("/_/stat") ||
        s.match?(/embedly|\bembed\b|emoji|avatar/)
    end

    srcs.find { |s| s.match?(%r{//(?:cdn-images-\d+|miro)\.medium\.com/}) } ||
      srcs.find { |s| s.match?(/\.(?:png|jpe?g|gif|webp)/i) }
  end
end

class ExternalPostProcessor < Jekyll::Generator
  safe true
  priority :low

  def generate(site)
    posts = site.posts.docs

    byline = ExternalPostThumbnails.site_byline(site)

    native_titles = posts.reject { |d| ExternalPostThumbnails.external?(d) }
                         .map { |d| ExternalPostThumbnails.title_key(d.data["title"], byline) }
                         .to_set

    dropped = 0
    thumbed = 0

    # reject! preserves the order of the kept docs (Jekyll's date sort stays valid).
    posts.reject! do |doc|
      next false unless ExternalPostThumbnails.external?(doc)

      if native_titles.include?(ExternalPostThumbnails.title_key(doc.data["title"], byline))
        dropped += 1
        Jekyll.logger.info "ExternalPosts:", "drop duplicate of native post -> #{doc.data['title']}"
        true # remove the Medium import; native post wins
      else
        if doc.data["thumbnail"].to_s.strip.empty?
          img = ExternalPostThumbnails.first_image(doc.content)
          if img
            doc.data["thumbnail"] = img
            thumbed += 1
          end
        end
        false # keep
      end
    end

    Jekyll.logger.info "ExternalPosts:", "dropped #{dropped} duplicate(s), set #{thumbed} thumbnail(s)"
  end
end
