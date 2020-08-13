# Building Docs

## Install jekyll
```bash
sudo apt-get install ruby-full build-essential zlib1g-dev
echo '# Install Ruby Gems to ~/gems' >> ~/.bashrc
echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
gem install jekyll bundler
```

## Build Docs

```bash
cd doc
rm Gemfile.lock
bundle install
bundle exec jekyll build
# Or for interactive docs update:
bundle exec jekyll serve
```
