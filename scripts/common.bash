set -eo pipefail

[[ "$TRACE" ]] && set -x

export CI_CONTAINER_NAME="ci_job_build_$CI_BUILD_ID"
export CI_REGISTRY_TAG="$CI_BUILD_REF_SLUG"

ensure_environment_url() {
  # [[ -n "$CI_ENVIRONMENT_URL" ]] && return

#  echo "Reading CI_ENVIRONMENT_URL from .gitlab-ci.yml..."
#  CI_ENVIRONMENT_URL="$(ruby -ryaml -e 'puts YAML.load_file(".gitlab-ci.yml")[ENV["CI_BUILD_NAME"]]["environment"]["url"]')"
#  CI_ENVIRONMENT_URL="$(eval echo "$CI_ENVIRONMENT_URL")"
  echo "CI_ENVIRONMENT_URL: $CI_ENVIRONMENT_URL"
}

ensure_deploy_variables() {
  if [[ -z "$CI_ENVIRONMENT_SLUG" ]]; then
    echo "Missing CI_ENVIRONMENT_SLUG."
    exit 1
  fi

  if [[ -z "$CI_ENVIRONMENT_URL" ]]; then
    echo "Missing CI_ENVIRONMENT_URL."
    exit 1
  fi
}

